import { Component, Input } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Title } from '@angular/platform-browser';

import { TranslateService } from '@ngx-translate/core';

import { UserRepositoryService } from 'app/core/repositories/users/user-repository.service';
import { BaseViewComponent } from 'app/site/base/base-view';
import { ViewBasePoll } from 'app/site/polls/models/view-base-poll';
import { ViewUser } from 'app/site/users/models/view-user';

@Component({
    selector: 'os-poll-progress',
    templateUrl: './poll-progress.component.html',
    styleUrls: ['./poll-progress.component.scss']
})
export class PollProgressComponent extends BaseViewComponent {
    @Input()
    public set poll(value: ViewBasePoll) {
        this._poll = value;

        // We cannot use this.poll.votescast during the voting, since it can
        // be reported with false values from the server
        const ids = new Set();
        for (const option of this.poll.options) {
            for (const vote of option.votes) {
                if (vote.user_id) {
                    ids.add(vote.user_id);
                }
            }
        }
        this.votescast = ids.size;

        this.calculateMaxUsers();
    }
    public get poll(): ViewBasePoll {
        return this._poll;
    }
    private _poll: ViewBasePoll;

    public votescast: number;
    public max: number;
    public valueInPercent: number;

    public constructor(
        title: Title,
        protected translate: TranslateService,
        snackbar: MatSnackBar,
        private userRepo: UserRepositoryService
    ) {
        super(title, translate, snackbar);
        this.userRepo
            .getViewModelListObservable()
            .subscribe(users => {
                if (users) {
                    this.calculateMaxUsers(users);
                }
            });
    }

    private calculateMaxUsers(allUsers?: ViewUser[]): void {
        if (!this.poll) {
            return;
        }
        if (!allUsers) {
            allUsers = this.userRepo.getViewModelList();
        }

        allUsers = allUsers.filter(user => user.is_present && this.poll.groups_id.intersect(user.groups_id).length)

        this.max = allUsers.length;
        this.valueInPercent = this.poll ? (this.votescast / this.max) * 100 : 0;
    }
}
